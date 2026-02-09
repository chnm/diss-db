# duplicate pairs were manually compiled through analyzing possible duplicates in the Django admiin. 
from django.db import migrations

# (scholar_to_delete_id, scholar_to_keep_id)
DUPLICATE_PAIRS = [
    (59503, 19250),  # de Grazia, Victoria
    (59118, 26746),  # Rubenstein, Anne
    (25667, 59603),  # Newfont, Kathryn
    (10092, 58541),  # Logevall, Fredrik
    (44557, 44558),  # Kellogg, Nelson R.
    (59711, 10861),  # Kashani-Sabet, Firoozeh
    (41315, 18283),  # Graham, Sandra Lauderdale
    (59611, 20733),  # Goucher, Candice
    (59436, 18986),  # Burds, Jeffrey
    (33952, 58533),  # Bailey, Johnny
    (54055, 32329),  # Smith, Thomas M., Jr.
    (58291, 29434),  # Johnston, Wade R.
    (43732, 43733),  # Jackson, Martin Alan
    (58673, 27634),  # Downey, D. Allan
    (54226, 59484),  # Sorrenson, Richard
    (54189, 13450),  # Somner, Matthew
    (38920, 59821),  # Dupuis, Serge
    (37754, 59510),  # Cullen, David O.
    (56870, 23425),  # Wiest, Andrew
    (8597, 58528),   # Studnicki-Gizbert, Daviken F.
]


def merge_scholars(apps, schema_editor):
    """
    Merge duplicate scholar records.
    
    For each pair, this function:
    1. Handles dissertations: transfers if only delete has one, deletes duplicate if both have one
    2. Transfers committee memberships, resolving conflicts by keeping the higher role
    3. Deletes the duplicate scholar record
    """
    Scholar = apps.get_model('dissdb', 'Scholar')
    Dissertation = apps.get_model('dissdb', 'Dissertation')
    CommitteeMember = apps.get_model('dissdb', 'CommitteeMember')
    
    # Role hierarchy for conflict resolution (chair > reader)
    ROLE_PRIORITY = {'chair': 2, 'reader': 1}
    
    for scholar_to_delete_id, scholar_to_keep_id in DUPLICATE_PAIRS:
        try:
            scholar_to_delete = Scholar.objects.get(pk=scholar_to_delete_id)
            scholar_to_keep = Scholar.objects.get(pk=scholar_to_keep_id)
        except Scholar.DoesNotExist as e:
            print(f"WARNING: Scholar not found for pair ({scholar_to_delete_id}, {scholar_to_keep_id}): {e}")
            continue
        
        print(f"Merging Scholar {scholar_to_delete_id} into {scholar_to_keep_id}...")
        
        # 1. Handle dissertations
        delete_dissertations = Dissertation.objects.filter(author=scholar_to_delete)
        keep_has_dissertation = Dissertation.objects.filter(author=scholar_to_keep).exists()
        
        if delete_dissertations.exists() and keep_has_dissertation:
            # Both have dissertations - delete the duplicate's dissertation
            # First, delete any committee members associated with the duplicate dissertation
            for diss in delete_dissertations:
                committee_deleted = CommitteeMember.objects.filter(dissertation=diss).delete()[0]
                if committee_deleted:
                    print(f"  - Deleted {committee_deleted} committee member(s) from duplicate dissertation")
            
            diss_deleted = delete_dissertations.delete()[0]
            print(f"  - Deleted {diss_deleted} duplicate dissertation(s)")
        elif delete_dissertations.exists():
            # Only scholar_to_delete has dissertation - transfer it
            dissertations_updated = delete_dissertations.update(author=scholar_to_keep)
            print(f"  - Transferred {dissertations_updated} dissertation(s)")
        
        # 2. Transfer committee memberships
        committee_memberships = CommitteeMember.objects.filter(scholar=scholar_to_delete)
        
        for membership in committee_memberships:
            # Check if scholar_to_keep already has a membership for this dissertation
            existing_membership = CommitteeMember.objects.filter(
                scholar=scholar_to_keep,
                dissertation=membership.dissertation
            ).first()
            
            if existing_membership:
                # Conflict: both scholars served on the same committee
                # Keep the one with the higher role (chair > reader)
                existing_priority = ROLE_PRIORITY.get(existing_membership.role, 0)
                incoming_priority = ROLE_PRIORITY.get(membership.role, 0)
                
                if incoming_priority > existing_priority:
                    # The one being deleted has a higher role, so update the keeper's role
                    print(f"  - Upgrading role for dissertation {membership.dissertation_id}: {existing_membership.role} -> {membership.role}")
                    existing_membership.role = membership.role
                    existing_membership.save()
                else:
                    print(f"  - Keeping existing {existing_membership.role} role for dissertation {membership.dissertation_id}")
                
                # Delete the duplicate membership
                membership.delete()
            else:
                # No conflict, just reassign the membership
                print(f"  - Transferred committee membership for dissertation {membership.dissertation_id}")
                membership.scholar = scholar_to_keep
                membership.save()
        
        # 3. Delete the duplicate scholar
        scholar_to_delete.delete()
        print(f"  - Deleted Scholar {scholar_to_delete_id}")
    
    print(f"\nCompleted merging {len(DUPLICATE_PAIRS)} duplicate pairs.")


def reverse_merge(apps, schema_editor):
    """
    This migration cannot be fully reversed because we delete records.
    Raise an error to prevent accidental reversal.
    """
    raise RuntimeError(
        "This migration cannot be reversed. "
        "Restore from a database backup if you need to undo these changes."
    )


class Migration(migrations.Migration):
    
    dependencies = [
        ('dissdb', '0011_duplicatecandidate'),
    ]
    
    operations = [
        migrations.RunPython(merge_scholars, reverse_merge),
    ]